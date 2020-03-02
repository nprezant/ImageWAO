
def saveManyImages(saveObjects:list):
    '''
    Saves many images in a multiprocessed fashion.
    `saveObjects`: list of tuples (object, [args]) where the
    object implements a `save` method, accepting `*[args]`
    as the parameter.
    '''
    for img, args in saveObjects:
        img.save(*args)
