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



// User likes/unlikes an image
export const handleLike = async (id, user, db, setImages, setSelectedImage) => {
    const docRef = db.collection('images').doc(id);
    const doc = await docRef.get();
    const data = doc.data();
    console.log(data);
    const likes = data.likes || [];
    const imageClass = data.metadata.predicted_class; // Assuming 'predicted_class' is the field you want to use

if (likes.includes(user.uid)) {
    await docRef.update({ likes: firebase.firestore.FieldValue.arrayRemove(user.uid) });
    // If unliking, you may want to decrement the score for the image class in user preferences.
    updateUserPreferences(user.uid, imageClass, 'decrement', db);
} else {
    await docRef.update({ likes: firebase.firestore.FieldValue.arrayUnion(user.uid) });
    // If liking, increment the score for the image class in user preferences.
    updateUserPreferences(user.uid, imageClass, 'increment', db);
}

    setImages((prevImages) =>
        prevImages.map((image) =>
            image.id === id ? { ...image, likes: likes.includes(user.uid) ? likes.filter(uid => uid !== user.uid) : [...likes, user.uid] } : image
        )
    );

    setSelectedImage((prevSelectedImage) =>
        prevSelectedImage && prevSelectedImage.id === id
            ? { ...prevSelectedImage, likes: likes.includes(user.uid) ? likes.filter(uid => uid !== user.uid) : [...likes, user.uid] }
            : prevSelectedImage
    );
};




// User preferences
export const updateUserPreferences = async (userId, imageClass, action, db) => {
    const userRef = db.collection('users').doc(userId);
    const userDoc = await userRef.get();

    if (!userDoc.exists) {
        console.log('No such user!');
        return;
    }

    let preferences = userDoc.data().preferences || {};
    let currentScore = preferences[imageClass] || 0;

    // Increment or decrement the score based on the action
    preferences[imageClass] = action === 'increment' ? currentScore + 1 : Math.max(currentScore - 1, 0);

    // Update the user's preferences
    await userRef.update({ preferences });
};



/*
// Display User preferences
function fetchAndDisplayUserPreferences(userId) {
    const userRef = db.collection('users').doc(userId);

    userRef.get().then(doc => {
        if (doc.exists) {
            const preferences = doc.data().preferences;
            // Sort the preferences by score
            const sortedPreferences = Object.entries(preferences).sort((a, b) => b[1] - a[1]);

            // Display the preferences in your React component
            // You might map over sortedPreferences and render them
        }
    }).catch(error => {
        console.log('Error getting document:', error);
    });
}
*/
