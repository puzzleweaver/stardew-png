# Stardew PNG

The end goal here is a nice static webpage for querying stardew valley sprites. That ended up wanting a bunch of utilities for unpacking and categorizing sprites from sheets.

## The Scripts and what they're for

#### `src/unpack.py`

For unpacking sprite sheets. It takes in sprite sheets from `raw_content` and outputs individual sprites under `output`.

#### `src/tag.py`

For tagging the individual images under `output`, sheet by sheet.

#### `src/mass_ops.py`

For doing global operations on the entire sprite dataset, stuff like adding or removing tags from everything with certain other tags, recropping all the sprites, listing global information about the tags that have been assigned, etc. It also has commands like `export`, for compiling the data in `output` into a frontend-consumable form in `exported`.

## How to Set Up your Environment (for Nanner)

To start, you'll want to set up a virtual environment. That looks like:

```
    python(3) -m venv venv
    source venv/bin/activate
```

If you're using `python3`, then you'll want to use that in the command above. But once you've run this, everything will just use `python` and `pip`. You might need to run `pip install` also, I'm not sure.

But yeah then call `python src/unpack.py raw_content/<category>` to run the unpacker or `python src/tag.py output/<category>` to run the tagger. Be really careful when using the tagger, because at least right now it's not super easy to undo mistakes.