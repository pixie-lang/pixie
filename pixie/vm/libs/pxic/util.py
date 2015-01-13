

read_handlers = {}
write_handlers = {}

def add_marshall_handlers(tp, write, read):
    read_handlers[tp] = read
    write_handlers[tp] = write

