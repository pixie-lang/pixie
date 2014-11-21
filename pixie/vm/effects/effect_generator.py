import pixie.vm.effects.effects as effect
import inspect


def munge(s):
     return s.replace("-", "_").replace("?", "_QMARK_").replace("!", "_BANG_")

_preamble="""
from pixie.vm.persistent_instance_hash_map import EMPTY as EMPTY_MAP

class {klass_name}(Effect):
     _immutable_ = True
     _type = Type(u"{type_name}")

     def type(self):
         return {klass_name}._type

     def __init__(self, {member_list}, mp=EMPTY_MAP):
         {self_member_list} = {member_list_unpack}
         self.__map = mp

     def get(self, k):
"""

_getter="""
         if k is {kw_name}:
             return self.{member_name}

"""

_getter_postlude="""
         return self.__map.val_at(k, None)

     def assoc(self, k, v):
"""

_assoc="""
         if k is {kw_name}:
             return {klass_name}({pre_members} v {post_members}, self.__map)

"""

_assoc_postlude="""

         return {klass_name}({members}, self.__map.assoc(k, v))

"""


def defeffect(name, klass_name, members):
    from pixie.vm.keyword import keyword
    members.append("k")
    gbls = inspect.currentframe().f_back.f_globals
    gbls["Effect"] = effect.Effect
    gbls["Type"] = effect.Type

    for x in members:
        gbls["KW_" + munge(x).upper()] = keyword(x)


    munged_members = map(munge, members)
    data = []
    data.append(_preamble.format(klass_name=klass_name,
                                 type_name=name,
                                 member_list=", ".join(map(lambda x: "w_" + x + (" = answer_k" if x == "k" else ""), munged_members)),
                                 member_list_unpack=", ".join(map(lambda x: "w_" + x, munged_members)),
                                 self_member_list=", ".join(map(lambda x: "self._w_" + x, munged_members))))
    for member in munged_members:
        data.append(_getter.format(kw_name="KW_" + member.upper(),
                                   member_name="_w_" + member))
    data.append(_getter_postlude)

    for idx in range(len(munged_members)):
        data.append(_assoc.format(kw_name="KW_" + munged_members[idx].upper(),
                                  klass_name=klass_name,
                                  pre_members=", ".join(map(lambda x: "self._w_" + x, munged_members[:idx])) + ("" if idx == 0 else ", "),
                                  post_members=(("" if idx + 1 == len(members) else ", ") + ", ".join(map(lambda x: "self._w_" + x, munged_members[idx + 1:])))
                                  ))

    data.append(_assoc_postlude.format(klass_name=klass_name,
                                       members=", ".join(map(lambda x: "self._w_" + x, munged_members))))

    s = "".join(data)

    print s

    exec s in gbls
