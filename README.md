# TSL-Conenct
TSL Connect is the Thai Sign Language Detection website that can recognition gesture through webcam in real-time. In TSL Connect, we chose 9 Thai alphabets and 6 vowels that have the highest frequency of occurrence.
<img width="1323" alt="Screenshot 2566-12-02 at 20 19 11" src="https://github.com/nichakontae/TSL-Conenct/assets/91275476/20fe44c4-58a6-4fe4-a4e8-240d55b6172a">


## Installation
Installing dependencies
```
pip install -r requirements.txt
```

running the server
```
python object_detector.py
```
## Images
Homepage
<img width="1440" alt="Screenshot 2566-12-02 at 19 43 01" src="https://github.com/nichakontae/TSL-Conenct/assets/91275476/0af167b0-dcea-4a8f-8742-3cda4dfd2a48">

when you open the home page, you need to make sure that it successfully connect with the socketio. If it successfully connect to socketio, it will show snackbar at the bottom left of screen
<img width="1440" alt="Screenshot 2566-12-02 at 19 42 43" src="https://github.com/nichakontae/TSL-Conenct/assets/91275476/b5ff05c5-b8f8-4451-80f5-da9515607b8b">

show the Thai Sign Language gesture to the webcam, it will show the bounding box and predict class on the screen.
<img width="1440" alt="Screenshot 2566-12-02 at 19 43 35" src="https://github.com/nichakontae/TSL-Conenct/assets/91275476/6b208676-911e-469b-b2b1-d264c31919e6">
