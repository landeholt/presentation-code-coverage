dev:
	ptw --runner "pytest --testmon";
covyore:
	tooling/covyore.py update;
	tooling/covyore.py check;
