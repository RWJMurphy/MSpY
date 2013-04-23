MSpY
====

A python class for scraping pricing and other data from msy.com.au

Usage
=====

    from mspy import MSpY

    mspy = MSpY()
    for product in mspy.products("RAM"):
        print("{p[size]}GB {p[ddr]} {p[clock]}MHz, ${p[price]:0.2f}".format(p=product))

