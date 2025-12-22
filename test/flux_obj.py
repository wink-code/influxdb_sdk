FLUX_DICT = {

}



class FieldStucture:
    '''
    Base class that is to organize fields.
    '''
    def __set_name__(self, cls, name):
        self.p_name = f'_{name}'




class FluxStructure:
    '''
    Descriptor that is designed to organize flux elements.
    '''
    _fmt = ''
    _fields = []
    

    def __init__(self, *args, **kwargs):
        if len(args) > self._fields:
            raise TypeError('Expected {} arguements.'.format(len(self._fields)))
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        for name in self._fields[len(args):]:
            value = kwargs.pop(name)
            setattr(self, name, value)
        if kwargs:
            raise TypeError('Invalid arguement(s): {}'.format(','.join(kwargs)))
        self._inner = ','.join(f'{field}:"{{field}}"' for field in self._fields)

    def __format__(self):
        return self._fmt.format()

if __name__ == '__main__':
    class AggregateWindow(FluxStructure):
        _fields = ['every','fn','createEmpty']
        _fmt = 'AggregateWindow({})'