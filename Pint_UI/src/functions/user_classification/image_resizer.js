import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import '../../App.css';

import { auth } from '../../firebaseAuth';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
import 'firebase/compat/firestore';
import 'firebase/compat/storage';
import Modal from 'react-modal';


export function resizeImage(file, maxWidth, maxHeight, callback) {
    const reader = new FileReader();
    reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;

            if (width > height) {
                if (width > maxWidth) {
                    height *= maxWidth / width;
                    width = maxWidth;
                }
            } else {
                if (height > maxHeight) {
                    width *= maxHeight / height;
                    height = maxHeight;
                }
            }

            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob((blob) => {
                callback(blob);
            }, 'image/jpeg', 0.85); // Adjust the quality parameter as needed
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}
