# Stardew PNG

The end goal here is a nice static webpage for querying stardew valley sprites.

## How to Unpack or Tag

To start, you'll want to set up a virtual environment. That looks like:

```
    python(3) -m venv venv
    source venv/bin/activate
```

If you're using `python3`, then you'll want to use that in the command above. But once you've run this, everything will just use `python` and `pip`. You might need to run `pip install` also, I'm not sure.

But yeah then call `python src/unpack.py raw_content/<category>` to run the unpacker or `python src/tag.py output/<category>` to run the tagger. Be really careful when using the tagger, because at least right now it's not super easy to undo mistakes.