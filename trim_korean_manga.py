#! /usr/bin/env python

import os
from tqdm import tqdm
import queue, threading

# removes empty horizontal filling in Korean manga
# required: imagemagick, fdupes
# put the script into the dir with the images 

# number of horizontal strips to cut image to
manga_strips = 77
thread_count = 4

tmp_dir = '/tmp/dev/manga/'

def worker():
	queue_full = True
	pbar_thread = tqdm(total=manga_strips, ascii=' .')
	
	while queue_full:
		try:
			filename = q.get(False)
			filename_split = filename.rsplit('.', 1)
			pbar_thread.reset()
			
			tmp_dir2 = tmp_dir + filename
			os.makedirs(tmp_dir2, exist_ok=True)
						
			os.system('convert "{filename}" -crop 1x{manga_strips}@ +repage "{tmp_dir2}/{filename_split[0]}.manga_strips.%03d.{filename_split[1]}" > /dev/null 2>&1'.format(
				filename=filename,
				manga_strips=manga_strips,
				tmp_dir2=tmp_dir2,
				filename_split=filename_split
			))
			
			for fi in range(manga_strips):				
				fi_f = tmp_dir2 + '/' + filename_split[0] + '.manga_strips.' + '%03d.' % fi + filename_split[1]
				
				# removing white stuff
				os.system('convert \( "' + fi_f + '" -bordercolor white -border 1x0 \) -size 1x1 xc:black -gravity west -composite -size 1x1 xc:black -gravity east -composite -fuzz 20% -trim +repage -bordercolor white -shave 1x0 "' + fi_f + '" > /dev/null 2>&1')
				# removing black stuff
				os.system('convert \( "' + fi_f + '" -bordercolor black -border 1x0 \) -size 1x1 xc:white -gravity west -composite -size 1x1 xc:white -gravity east -composite -fuzz 20% -trim +repage -bordercolor black -shave 1x0 "' + fi_f + '" > /dev/null 2>&1')
				
				pbar_thread.update(1)
			
			os.system('fdupes -d -N "%s" > /dev/null 2>&1' % tmp_dir2)
			os.system('convert "' + tmp_dir2 + '/' + filename_split[0] + '.manga_strips.*" -append "done/' + filename + '"  > /dev/null 2>&1')
			
			os.system('cd "%s"; rm "%s"* > /dev/null 2>&1' % (tmp_dir2, filename_split[0]))
			os.system('rmdir "%s" > /dev/null 2>&1' % tmp_dir2)
			
			pbar.update(1)
		except queue.Empty:
			queue_full = False	


if tmp_dir[-1] != '/':
	tmp_dir += '/'

os.makedirs(tmp_dir, exist_ok=True)
os.makedirs('done', exist_ok=True)

filenames = [ x for x in os.listdir('./') if os.path.isfile(x) and x not in ('trim_korean_manga.py') ]
filenames = sorted(filenames)

pbar = tqdm(total=len(filenames), desc='Images')

q = queue.Queue()
threads = []

for f in filenames:
	q.put(f)
	
for i in range(thread_count):
	t = threading.Thread(target=worker)
	t.start()
	threads.append(t)

for t in threads:
	t.join()

pbar.close()

os.system('notify-send "done"')
