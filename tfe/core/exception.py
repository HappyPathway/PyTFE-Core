class TFEException(Exception): pass
class TFESessionException(Exception): pass
class TFEValidationError(Exception): pass
class TFEAttributeError(Exception): pass
    
def exc(original_function):                            
    def new_function(*args,**kwargs):      
        try:             
            x = original_function(*args,**kwargs)                    
            return x
        except Exception as e:
            exception_name = e.__class__.__name__
            raise type("TFE{0}".format(exception_name), (TFEException, e.__class__), dict())(str(e))                                     
    return new_function  

def RaisesTFEException(Cls):
    class NewCls(object):
        
        def __init__(self,*args,**kwargs):
            self.oInstance = Cls(*args,**kwargs)

        def __getattribute__(self,s):
            try:    
                x = super(NewCls,self).__getattribute__(s)
            except AttributeError:      
                pass
            else:
                return x
            try:
                x = self.oInstance.__getattribute__(s)
            except AttributeError as e:
                raise type("TFEAttributeError", (TFEException, AttributeError), dict())(str(e))
            if type(x) == type(self.__init__): # it is an instance method
                return exc(x)                 # this is equivalent of just decorating the method with time_this
            else:
                return x
    return NewCls
