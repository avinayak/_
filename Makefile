PROJECT_NAME := moodle

.PHONY: start download download-run-deploy

download:
	python3 downloader.py https://www.pinterest.jp/atulvinayak/pins/ -d docs/images

run: 
	python generate.py 

download-run-deploy:
	python3 downloader.py https://www.pinterest.jp/atulvinayak/pins/ -j 16 -d docs/images \
	&& python generate.py \
	&& git add -A \
	&& git commit -am "_" \
	&& sleep 3 \
	&& git push

deploy:
	git add -A \
	&& git commit -am "_" \
	&& sleep 3 \
	&& git push