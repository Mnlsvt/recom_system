import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import './App.css';

import { auth } from './firebaseAuth';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';

// Sample data
const initialImages = [
    { id: 1, url: '/test_images/beach.jpg', likes: 0 },
    { id: 2, url: '/test_images/farm.jpeg', likes: 0 },
    { id: 3, url: '/test_images/amsterdam.jpeg', likes: 0 },
    { id: 4, url: '/test_images/gkotzostrena.jpg', likes: 0 },
    { id: 5, url: '/test_images/hair_salon.jpeg', likes: 0 },
    { id: 6, url: '/test_images/london.jpg', likes: 0 },
    { id: 7, url: '/test_images/palia_spitia.jpeg', likes: 0 },
    { id: 8, url: '/test_images/street2.jpeg', likes: 0 },
    { id: 9, url: '/test_images/street3.jpg.jpeg', likes: 0 },
    { id: 10, url: '/test_images/street.jpeg', likes: 0 },
    { id: 11, url: '/test_images/trena2.jpg', likes: 0 },
    { id: 12, url: '/test_images/trena.jpg', likes: 0 },
    { id: 13, url: '/test_images/tzalliaschorus.jpg', likes: 0 },
    { id: 14, url: '/test_images/tzalliasdromos.jpg', likes: 0 },
    { id: 15, url: '/test_images/tzallias.jpg', likes: 0 },


    // add more image objects...
];


function SignInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider);
}

function SignInWithEmailPassword(email, password) {
    auth.signInWithEmailAndPassword(email, password);
}

function SignUpWithEmailPassword(email, password) {
    auth.createUserWithEmailAndPassword(email, password);
}

function SignUpPage() {
    return (
        <div className="signup-form">
            <h2>Sign Up</h2>
            <form onSubmit={(e) => {
                e.preventDefault();
                SignUpWithEmailPassword(e.target.email.value, e.target.password.value);
            }}>
                <input name="email" type="email" placeholder="Email" />
                <input name="password" type="password" placeholder="Password" />
                <button type="submit">Sign up</button>
            </form>
        </div>
    );
}


function App() {
    const [images, setImages] = useState(initialImages);
    const [selectedImage, setSelectedImage] = useState(null);
    const [isExpanded, setExpanded] = useState(false);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged((user) => {
            if (user) {
                setUser(user);
            } else {
                setUser(null);
            }
        });


        return () => unsubscribe();
    }, []);

    const handleLike = (id) => {
        setImages((prevImages) =>
            prevImages.map((image) =>
                image.id === id ? { ...image, isLiked: !image.isLiked } : image
            )
        );

        setSelectedImage((prevSelectedImage) =>
            prevSelectedImage && prevSelectedImage.id === id
                ? { ...prevSelectedImage, isLiked: !prevSelectedImage.isLiked }
                : prevSelectedImage
        );
    };

    const handleSelect = (image) => {
        setSelectedImage(image);
        setExpanded(true);
    };

    const handleDeselect = () => {
        setSelectedImage(null);
        setExpanded(false);
    };

    const handleSignOut = () => {
        auth.signOut();
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Ptuxiakh Manwlh</h1>
                {user && (
                    <div className="user-info">
                        <img src={user.photoURL} alt="User" />
                        <span>{user.displayName}</span>
                        <button className="logout-button" onClick={handleSignOut}>Logout</button>
                    </div>
                )}
            </header>
            {user ? (
                // User is signed in, render the main app
                <div className="masonry">
                    {images.map(image => (
                        <div key={image.id} className="image-item" onClick={() => handleSelect(image)}>
                            <img src={image.url} alt="" />
                            <div className="image-item-info">
                                <button onClick={(e) => { e.stopPropagation(); handleLike(image.id); }}>
                                    {image.isLiked ? "❤️" : "🤍"}
                                </button>
                            </div>
                        </div>
                    ))}
                    {selectedImage && isExpanded && (
                        <div className="expandedImage" onClick={(e) => e.target === e.currentTarget && handleDeselect()}>
                            <div className="expandedImageContainer">
                                <img src={selectedImage.url} alt="" />
                                <div className="image-item-info">
                                    <button onClick={(e) => { e.stopPropagation(); handleLike(selectedImage.id); }}>
                                        {selectedImage.isLiked ? "❤️" : "🤍"}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            ) : (
// User is signed out, render the sign in/sign up forms
                <div className="login-form">
                    <h2>Sign In</h2>
                    <button onClick={SignInWithGoogle}>Sign in with Google</button>
                    <form onSubmit={(e) => {
                        e.preventDefault();
                        SignInWithEmailPassword(e.target.email.value, e.target.password.value);
                    }}>
                        <input name="email" type="email" placeholder="Email" />
                        <input name="password" type="password" placeholder="Password" />
                        <button type="submit">Sign in</button>
                    </form>
                    <h2>Sign Up</h2>
                    <form onSubmit={(e) => {
                        e.preventDefault();
                        SignUpWithEmailPassword(e.target.email.value, e.target.password.value);
                    }}>
                        <input name="email" type="email" placeholder="Email" />
                        <input name="password" type="password" placeholder="Password" />
                        <button type="submit">Sign up</button>
                    </form>
                </div>
            )}
        </div>
    );
}

export default App;
