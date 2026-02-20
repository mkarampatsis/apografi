import mongoengine as me
from models.sdad.organizations import Organizations
from models.sdad.organizational_units import Organizational_Units
from models.psped.monada import Monada

class TreeNode(me.EmbeddedDocument):
  expandable = me.BooleanField()
  monada = me.ReferenceField(Organizational_Units)
  level = me.IntField()
  remitsFinalized = me.BooleanField()


def print_tree(node, indent=0):
  print("\t" * indent, node.id, node.preferredLabel)
  for subordinate in node.subordinates:
      print_tree(subordinate, indent + 1)


def build_subtree(super_monada, monades):
  subordinates = [u for u in monades if u.supervisorUnitCode == super_monada.code]

  for sub in subordinates:
      sub.subordinates = build_subtree(sub, monades)

  return subordinates


def build_tree(monades):
  roots = [u for u in monades if not u.supervisorUnitCode]

  for root in roots:
      root.subordinates = build_subtree(root, monades)
      # print_tree(root)

  return roots


def convert_tree_to_flat_nodes(node, level=0):
  monada = Monada.objects.get(code=node.code)
  flat_nodes = []
  flat_node = TreeNode(expandable=bool(node.subordinates), monada=node, level=level, remitsFinalized=monada.remitsFinalized)
  flat_nodes.append(flat_node)
  for subordinate in node.subordinates:
      flat_nodes.extend(convert_tree_to_flat_nodes(subordinate, level + 1))
  return flat_nodes


class Apografi(me.EmbeddedDocument):
  foreas = me.ReferenceField(Organizations)
  monades = me.ListField(me.ReferenceField(Organizational_Units))


class Foreas(me.Document):
  meta = {"collection": "foreis", "db_alias": "psped"}

  code = me.StringField(required=True, unique=True)
  level = me.StringField(
    choices=["ΚΕΝΤΡΙΚΟ", "ΑΠΟΚΕΝΤΡΩΜΕΝΟ", "ΠΕΡΙΦΕΡΕΙΑΚΟ", "ΤΟΠΙΚΟ", "ΜΗ ΟΡΙΣΜΕΝΟ"],
    default="ΜΗ ΟΡΙΣΜΕΝΟ",
  )
  provisionText = me.StringField()
  apografi = me.EmbeddedDocumentField(Apografi, required=True)
  tree = me.EmbeddedDocumentListField(TreeNode)

  def to_dict(self):
    return self.to_mongo().to_dict()

  def build_tree(self):
    monades = self.apografi.monades
    tree = build_tree(monades)

    flat_nodes = []
    for root in tree:
      flat_nodes.extend(convert_tree_to_flat_nodes(root))
    Foreas.objects(code=self.code).update_one(set__tree=flat_nodes)

  def tree_to_json(self):
    self.build_tree()
    tree = []
    for node in self.tree:
      tree.append(
        {
          "expandable": node.expandable,
          "monada": {
            "preferredLabel": node.monada.preferredLabel,
            "code": node.monada.code,
          },
          "level": node.level,
          "remitsFinalized": node.remitsFinalized
        }
      )
    return tree
