MSpY
====

A python class for scraping pricing and other data from msy.com.au

Usage
=====

    from mspy import MSpY

    mspy = MSpY()
    for product in mspy.products("RAM"):
        print("{p[size]}GB {p[ddr]} {p[clock]}MHz, ${p[price]:0.2f}".format(p=product))

Would print the following:

    1GB DDR2 800MHz, $15.00
    2GB DDR3 1333MHz, $16.00
    2GB DDR3 1333MHz, $17.00
    1GB DDR2 800MHz, $17.00
    2GB DDR3 1333MHz, $19.00
