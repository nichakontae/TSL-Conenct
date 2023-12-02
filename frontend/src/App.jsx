import React, { useState, useEffect } from "react";
import { useRef } from "react";
import { io } from "socket.io-client";
import { Box, Button, Stack, Typography } from "@mui/material";
import { useSnackbar } from "notistack";

const App = () => {
  const class_colors = {
    Mo: "#219733",
    No: "#0D5D07",
    O: "#6A7970",
    SaRaE: "#0F2E12",
    SaRaA: "#A8C41C",
    SaRaAr: "#122197",
    SaRaAe: "#A25E26",
    MaiHanAkat: "#912146",
    Ko: "#5D619D",
    Bo: "#881179",
    Wo: "#E84E02",
    Ya: "#711111",
    Lo: "#500630",
    Ro: "#D41C1C",
    MaiMaLai: "#19BBAC",
  };
  const [webcamOpen, setWebcamOpen] = useState(false);
  const [webcamInterval, setWebcamInterval] = useState(null);
  const { enqueueSnackbar } = useSnackbar();

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const socket = useRef(null);
  const boxes = useRef(null);
  const isSend = useRef(false);

  useEffect(() => {
    socket.current = io.connect(import.meta.env.VITE_SOCKETIO);
    socket.current.connect();
    socket.current.on("connected", function (data) {
      enqueueSnackbar("Successfully connect to socketio!", {
        variant: "success",
      });
    });

    socket.current.on("processed_image", function (data) {
      if (!webcamOpen) {
        boxes.current = data.boxes;
        isSend.current = false;
        drawImageAndBoxes();
      }
    });

    return () => {
      socket.current.disconnect();
    };
  }, []);

  const openWebcam = () => {
    const FPS = 10;
    const video = videoRef.current;

    if (!webcamOpen) {
      socket.current?.emit("create_folders");
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      canvas.style.display = "block";

      if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
          .getUserMedia({ video: true })
          .then(function (stream) {
            video.srcObject = stream;
            video.play();

            // Set up the interval only when the webcam is open
            setWebcamInterval(
              setInterval(() => {
                const width = canvas.width;
                const height = canvas.height;

                context.drawImage(video, 0, 0, width, height);

                if (!isSend.current) {
                  const data = canvasRef.current.toDataURL("image/jpeg", 1);
                  socket.current?.emit("image", data);
                  isSend.current = true;
                }

                if (boxes.current != null) {
                  drawImageAndBoxes();
                }
              }, 1000 / FPS)
            );
          })
          .catch(function (err0r) {
            console.error("Error accessing webcam: ", err0r);
          });
      } else {
        alert("getUserMedia is not supported in this browser");
      }
    } else {
      // video.style.display = "none";
      if (video.srcObject) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach((el) => el.stop());
      }
      // Reset bounding boxes when the webcam is closed
      boxes.current = [];
      drawImageAndBoxes();
      video.srcObject = null;
      const canvas = canvasRef.current;
      canvas.style.display = "none";
      const context = canvas.getContext("2d");
      context.clearRect(0, 0, canvas.width, canvas.height);

      // Clear the interval when the webcam is closed
      clearInterval(webcamInterval);
      socket.current?.emit("delete_folders");
    }

    setWebcamOpen(!webcamOpen);
    console.log("webcam status", webcamOpen);
  };

  const drawImageAndBoxes = () => {
    const canvas = canvasRef.current;

    if (!canvas) {
      console.error("Canvas reference is null");
      return;
    }

    const context = canvas.getContext("2d");
    if (!context) {
      console.error("2D context is null");
      return;
    }

    boxes.current.forEach(([x1, y1, x2, y2, label]) => {
      const color = class_colors[label];
      // Draw the existing boxes if new data has not arrived
      context.strokeStyle = color;
      context.lineWidth = 2;
      context.font = "15px serif";

      console.log(label);
      console.log(color);
      context.strokeRect(x1, y1, x2 - x1, y2 - y1);
      context.fillStyle = color;
      const width = context.measureText(label).width;
      context.fillRect(x1, y1, width + 10, 15);
      context.fillStyle = "#ffffff";
      context.fillText(label, x1 + 5, y1 + 12);
    });
  };

  return (
    <Box id="container" width={"100vw"} height="100vh">
      <Stack
        width={"100%"}
        height="100%"
        justifyContent={"center"}
        alignItems="center"
      >
        <canvas
          ref={canvasRef}
          id="canvas"
          style={{ width: "1000px", height: "700px", display: "none" }}
        ></canvas>
        <button
          id="buttonElement"
          onClick={openWebcam}
          type="button"
          style={{
            width: "18rem",
            height: "5rem",
            fontSize: "1.5rem",
            marginTop: webcamOpen ? "2rem" : "0rem",
          }}
        >
          {webcamOpen ? "Close Webcam" : "Open Webcam"}
        </button>
        <Typography
          variant="h6"
          sx={{ marginTop: "1rem" }}
          textAlign={"center"}
        >
          if you don't see any message for successfully connect to socketio,
          <br />
          please try to use another browser or another user account.
        </Typography>
      </Stack>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        id="videoElement"
        style={{ display: "none" }}
      ></video>
      <Stack
        direction={"row"}
        // justifyContent={"center"}
        alignItems={"center"}
        paddingY={"1rem"}
        sx={{ position: "absolute", bottom: "0rem", right: "46%" }}
      >
        <img src="/logo.png" width={30} />
        <Typography
          color={"black"}
          fontSize={"1.2rem"}
          fontWeight={"bold"}
          paddingLeft={"0.5rem"}
        >
          TSL Connect
        </Typography>
      </Stack>
    </Box>
  );
};

export default App;
