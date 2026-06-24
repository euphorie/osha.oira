from plone.namedfile.interfaces import INamedBlobImage


def is_image_small(context, fname="image"):
    image = getattr(context, fname, None)
    if image and INamedBlobImage.providedBy(image):
        x, y = image.getImageSize()
        if x < 1000 or y < 430:
            return True
