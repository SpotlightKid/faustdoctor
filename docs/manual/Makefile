PREFIX ?= /usr/local
DOCDIR ?= $(PREFIX)/share/doc
LANGS = en

all:
	$(foreach lang,$(LANGS),$(MAKE) -C $(lang);)

clean:
	$(foreach lang,$(LANGS),$(MAKE) -C $(lang) clean;)

install:
	install -dm 755 $(DESTDIR)$(DOCDIR)/faustdoctor/{eaxample,manual}
	install -Dm 744 examples/*.{dsp,txt} $(DESTDIR)$(DOCDIR)/faustdoctor/examples/
	$(foreach lang,$(LANGS),install -Dm 644 $(lang)/manual.html $(DESTDIR)$(DOCDIR)/faustdoctor/manual/$(lang)/manual.html;)
