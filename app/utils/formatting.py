def classes_text(count):
    """'1 class' / '2 classes' (fixes '1 classes')."""
    return f"{count} class" if count == 1 else f"{count} classes"
