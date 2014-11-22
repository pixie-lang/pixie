from pixie.vm.code import defprotocol, link_builtins

defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

defprotocol("pixie.stdlib", "ICounted", ["-count"])
defprotocol("pixie.stdlib", "IAssociative", ["-assoc", "-contains-key", "-dissoc"])

defprotocol("pixie.stdlib", "ILookup", ["-val-at"])

defprotocol("pixie.stdlib", "IMapEntry", ["-key", "-val"])

defprotocol("pixie.stdlib", "IStack", ["-push", "-pop"])

defprotocol("pixie.stdlib", "IFn", ["-invoke"])

#IVector = as_var("pixie.stdlib", "IVector")(Protocol(u"IVector"))

#IMap = as_var("pixie.stdlib", "IMap")(Protocol(u"IMap"))

defprotocol("pixie.stdlib", "IMeta", ["-with-meta", "-meta"])

defprotocol("pixie.stdlib", "ITransient", ["-persistent!"])
defprotocol("pixie.stdlib", "IToTransient", ["-transient"])

defprotocol("pixie.stdlib", "ITransientCollection", ["-conj!"])

defprotocol("pixie.stdlib", "IIterable", ["-iterator"])
defprotocol("pixie.stdlib", "IIterator", ["-current", "-at-end?", "-move-next!"])

link_builtins("-count", "count")
link_builtins("-first", "first")
link_builtins("-next", "next")

defprotocol("pixie.stdlib", "IIndexed", ["-nth"])

defprotocol("pixie.stdlib", "IPersistentCollection", ["-conj", "-disj"])

defprotocol("pixie.stdlib", "IEmpty", ["-empty"])

defprotocol("pixie.stdlib", "IObject", ["-hash", "-eq", "-str", "-repr"])
#_eq.set_default_fn(wrap_fn(lambda a, b: false))

defprotocol("pixie.stdlib", "IReduce", ["-reduce"])

defprotocol("pixie.stdlib", "IDeref", ["-deref"])

defprotocol("pixie.stdlib", "IReset", ["-reset!"])

defprotocol("pixie.stdlib", "INamed", ["-namespace", "-name"])
