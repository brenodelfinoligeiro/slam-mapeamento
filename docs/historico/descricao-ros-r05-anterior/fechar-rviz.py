"""WM_DELETE_WINDOW em servidor X privado de ensaio; não controla desktop do usuário."""
import ctypes as C

def fechar_rviz():
    x=C.CDLL('libX11.so.6');W=C.c_ulong;D=C.c_void_p
    x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=D
    x.XDefaultRootWindow.argtypes=[D];x.XDefaultRootWindow.restype=W
    x.XQueryTree.argtypes=[D,W,C.POINTER(W),C.POINTER(W),C.POINTER(C.POINTER(W)),C.POINTER(C.c_uint)]
    x.XFetchName.argtypes=[D,W,C.POINTER(C.c_char_p)];x.XFree.argtypes=[D]
    x.XInternAtom.argtypes=[D,C.c_char_p,C.c_int];x.XInternAtom.restype=W
    class Data(C.Union):_fields_=[('b',C.c_char*20),('s',C.c_short*10),('l',C.c_long*5)]
    class Client(C.Structure):_fields_=[('type',C.c_int),('serial',W),('send_event',C.c_int),('display',D),('window',W),('message_type',W),('format',C.c_int),('data',Data)]
    class Event(C.Union):_fields_=[('xclient',Client),('pad',C.c_long*24)]
    x.XSendEvent.argtypes=[D,W,C.c_int,C.c_long,C.POINTER(Event)];x.XFlush.argtypes=[D];x.XCloseDisplay.argtypes=[D]
    display=x.XOpenDisplay(None)
    if not display:raise RuntimeError('Sem servidor X privado')
    try:
        pending=[int(x.XDefaultRootWindow(display))];target=None
        for _ in range(512):
            if not pending:break
            win=pending.pop();name=C.c_char_p()
            if x.XFetchName(display,win,C.byref(name)) and name.value:
                title=name.value.decode(errors='replace');x.XFree(C.cast(name,D))
                if 'rviz' in title.lower():target=win;break
            root=W();parent=W();children=C.POINTER(W)();count=C.c_uint()
            if x.XQueryTree(display,win,C.byref(root),C.byref(parent),C.byref(children),C.byref(count)):
                pending.extend(int(children[i]) for i in range(count.value))
                if children:x.XFree(C.cast(children,D))
        if target is None:raise RuntimeError('Janela RViz não encontrada')
        event=Event();event.xclient.type=33;event.xclient.display=display;event.xclient.window=target;event.xclient.message_type=x.XInternAtom(display,b'WM_PROTOCOLS',0);event.xclient.format=32;event.xclient.data.l[0]=x.XInternAtom(display,b'WM_DELETE_WINDOW',0);event.xclient.data.l[1]=0
        assert x.XSendEvent(display,target,0,0,C.byref(event))!=0
        x.XFlush(display)
        return target
    finally:x.XCloseDisplay(display)
