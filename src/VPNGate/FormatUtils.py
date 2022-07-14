

def format_bytes(b: int):
	b = float(b)
	Kb = float(1024)
	Mb = float(Kb ** 2) # 1,048,576
	Gb = float(Kb ** 3) # 1,073,741,824
	Tb = float(Kb ** 4) # 1,099,511,627,776

	if b < Kb:
		return '{0} {1}'.format(b,'bytes' if 0 == b > 1 else 'byte')
	elif Kb <= b < Mb:
		return '{0:.2f} Kb'.format(b / Kb)
	elif Mb <= b < Gb:
		return '{0:.2f} Mb'.format(b / Mb)
	elif Gb <= b < Tb:
		return '{0:.2f} Gb'.format(b / Gb)
	elif Tb <= b:
		return '{0:.2f} Tb'.format(b / Tb)
