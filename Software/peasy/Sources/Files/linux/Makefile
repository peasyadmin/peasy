DYN_VERS_MAJ=1
DYN_VERS_MIN=0

VERSION=$(DYN_VERS_MAJ).$(DYN_VERS_MIN)
DESTDIR=/usr
PREFIX=

.PHONEY:	install
install:	$(DYNAMIC)
	@echo "[Install]"
	@install -m 0755 -d			$(DESTDIR)$(PREFIX)/bin
	@install -m 0755 -d			$(DESTDIR)$(PREFIX)/share
	@install -m 0755 -d			$(DESTDIR)$(PREFIX)/share/applications
	@install -m 0755 -d			$(DESTDIR)$(PREFIX)/share/arduino
	@install -m 0755 -d			$(DESTDIR)$(PREFIX)/share/arduino/libraries
	@cp -r EsPeEs/		$(DESTDIR)$(PREFIX)/share
	@install -m 0755 ../Files/Peasy/Peasy			$(DESTDIR)$(PREFIX)/bin
	@install -m 0755 ../Files/Peasy/Peasy-Server			$(DESTDIR)$(PREFIX)/bin
	@install -m 0755 ../Files/Peasy/Peasy.desktop		$(DESTDIR)$(PREFIX)/share/applications
	@ln -sf $(DESTDIR)$(PREFIX)/share/Peasy/EsPeEs4Arduino		$(DESTDIR)$(PREFIX)/share/arduino/libraries/EsPeEs4Arduino
	@ldconfig

.PHONEY:	uninstall
uninstall:
	@echo "[UnInstall]"
	@rm -f $(DESTDIR)$(PREFIX)/bin/Peasy
	@rm -f $(DESTDIR)$(PREFIX)/bin/Peasy-Server
	@rm -f $(DESTDIR)$(PREFIX)/share/applications/Peasy.desktop
	@rm -r $(DESTDIR)$(PREFIX)/share/arduino/libraries/EsPeEs4Arduino
	@rm -r $(DESTDIR)$(PREFIX)/share/Peasy
	@ldconfig
