import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor

def start(message, fs_videos, fs_mp3s, channel):
	message = json.loads(message)

	# empty temp file
	tf = tempfile.NamedTemporaryFile()

	# write video contents
	out = fs_videos.get(ObjectId(message['video_fid']))
	tf.write(out.read())

	# convert to mp3 from tf
	audio = moviepy.editor.VideoFileClip(tf.name).audio

	tf.close()

	# write mp3 contents
	tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
	audio.write_audiofile(tf_path)

	# save to mongodb
	f = open(tf_path, 'rb')
	data = f.read()
	fid = fs_mp3s.put(data)

	# remove temp file
	f.close()
	os.remove(tf_path)

	message['mp3_fid'] = str(fid)

	try:
		channel.basic_publish(
			exchange = "",
			routing_key = os.environ.get('MP3_QUEUE'),
			body = json.dumps(message),
			properties = pika.BasicProperties(
				delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE
			)
		)
	except Exception as e:
		fs_mp3s.delete(fid)
		return "Failed to publish message to MP3_QUEUE"