def main(argv=None):
    import sys
    from alpaca.admin.application import Application
    if argv is None:
        argv = sys.argv
    application = Application()
    application.run(argv)
