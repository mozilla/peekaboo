def patch():
    import jingo.monkey
    jingo.monkey.patch()

    import jingo
    from compressor.contrib.jinja2ext import CompressorExtension
    jingo.env.add_extension(CompressorExtension)

    import session_csrf
    session_csrf.monkeypatch()
