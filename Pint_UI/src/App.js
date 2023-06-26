import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './App.css';

import { auth } from './firebaseAuth';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
import 'firebase/compat/firestore';
import 'firebase/compat/storage';


// Initialization of Firebase and Firestore
const firebaseConfig = {
    apiKey: "AIzaSyDvKNc1V079WbA3B4CBHZAwqcxDcW8Cm7o",
    authDomain: "ptuxiakhmanwlhs.firebaseapp.com",
    projectId: "ptuxiakhmanwlhs",
    storageBucket: "ptuxiakhmanwlhs.appspot.com",
    messagingSenderId: "1086816491330",
    appId: "1:1086816491330:web:c7c9278565c6d2b86c5adb",
    measurementId: "G-K8S7N9DSZ7"
};
firebase.initializeApp(firebaseConfig);
//const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();



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

function Profile({ user, images, onDelete, onLike }) {
    const navigate = useNavigate();
    const userImages = images.filter(image => image.uploaderId === user.uid);

    const handleBack = () => {
        navigate('/');
    }

    const userImagesExists = userImages.filter(image => image.url); // Only images with url are included
    return (
        <div>
            <button onClick={handleBack} className="back-button">Back</button>
            <img src={user.photoURL} alt="User" />
            <h2>{user.displayName}'s Profile</h2>
            <div className="user-images">
                {userImagesExists.map(image => (
                    <div key={image.id} className="image-item">
                        <img src={image.url} alt="" />
                        <div className="image-item-info">
                            <button onClick={(e) => { e.stopPropagation(); onLike(image.id); }}>
                                {image.likes && image.likes.includes(user.uid) ? "❤️Like" : "🤍Like"}
                            </button>
                            <button className="trashButton" onClick={() => onDelete(image.id, image.url)}>🗑️Delete</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}



function Upload({ user }) {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [recentImageUrls, setRecentImageUrls] = useState([]);
    const navigate = useNavigate();

    const handleBack = () => {
        navigate('/');
    }

    /*
    const handleUpload = async () => {
        if (isLoading || !file) return;
        setIsLoading(true);
        const storageRef = storage.ref();
        const fileRef = storageRef.child(file.name);
        await fileRef.put(file);
        const fileUrl = await fileRef.getDownloadURL();
        setRecentImageUrls(prevUrls => [fileUrl, ...prevUrls]);

        await db.collection('images').add({
            url: fileUrl,
            uploaderId: user.uid,
            likes: []
        });
        setIsLoading(false);
        setFile(null);
    };
    */

    const handleUpload = async () => {
        if (isLoading || !file) return;
        setIsLoading(true);

        const fileExtension = file.name.split('.').pop();

        // Save the image data in Firestore, excluding the tags
        const imageDoc = await db.collection('images').add({
            uploaderId: user.uid,
            likes: [],
            extension: fileExtension  // Save the file extension in Firestore
        });

        const storageRef = storage.ref();
        const fileRef = storageRef.child(`${imageDoc.id}.${fileExtension}`);  // Append the extension to the file name
        await fileRef.put(file);
        const fileUrl = await fileRef.getDownloadURL();
        setRecentImageUrls(prevUrls => [fileUrl, ...prevUrls]);

        await db.collection('images').doc(imageDoc.id).update({ url: fileUrl }); // Update the URL in the document

        // Create a FormData object, append the file and the image id
        const formData = new FormData();
        formData.append('file', file);
        formData.append('image_id', imageDoc.id);

        // Make a POST request to the Python server
        //await fetch('https://metadata-generator-ghqsm.run-eu-central1.goorm.site/predict', {
        //    method: 'POST',
        //    body: formData
        //});
        navigator.sendBeacon('https://metadata-gen-mguay.run-eu-central1.goorm.site/predict', formData);

        setIsLoading(false);
        setFile(null);
    };




    return (
        <div>
            <button onClick={handleBack} className="back-button">Back</button>
            <input type="file" onChange={e => setFile(e.target.files[0])} />
            <button disabled={isLoading} onClick={handleUpload} className="upload-button">{isLoading ? 'Uploading...' : 'Upload'}</button>
            <div className="uploadImages">
                {recentImageUrls.map((url, index) => (
                    <div key={index} className="image-item">
                        <img src={url} alt="" />
                    </div>
                ))}
            </div>
        </div>
    );


}




function App() {
    const [images, setImages] = useState([]);
    //const [images, setImages] = useState(initialImages);
    const [selectedImage, setSelectedImage] = useState(null);
    const [isExpanded, setExpanded] = useState(false);
    const [user, setUser] = useState(null);
    const [showHeart, setShowHeart] = useState(false);

    useEffect(() => {
        const unsubscribe = auth.onAuthStateChanged((user) => {
            if (user) {
                setUser(user);
            } else {
                setUser(null);
            }
        });

        const fetchData = async () => {
            const data = await db.collection("images").get();
            setImages(data.docs.map(doc => ({ ...doc.data(), id: doc.id })));
        }
        fetchData();


        return () => unsubscribe();
    }, []);


    const handleLike = async (id) => {
        const docRef = db.collection('images').doc(id);
        const doc = await docRef.get();
        const likes = doc.data().likes || [];

        if (likes.includes(user.uid)) {
            await docRef.update({ likes: firebase.firestore.FieldValue.arrayRemove(user.uid) });
        } else {
            await docRef.update({ likes: firebase.firestore.FieldValue.arrayUnion(user.uid) });
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

    const handleDelete = async (id, url) => {
        const docRef = db.collection('images').doc(id);
        await docRef.delete();

        const imageRef = storage.refFromURL(url);
        await imageRef.delete();

        setImages(prevImages => prevImages.filter(image => image.id !== id));
    };


    const handleDoubleLike = (id) => {
        const selectedLikes = selectedImage.likes || [];
        if (!selectedLikes.includes(user.uid)) {
            handleLike(id);
            setShowHeart(true);
            setTimeout(() => setShowHeart(false), 1000);
        }
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


    // The profileButtonMain and uploadButtonMain are the button showing on the main page (when the user logs in)
    return (
        <Router>
            <div className="App">
                <header className="App-header">
                    <h1>Ptuxiakh Manwlh</h1>
                    {user && (
                        <div >
                            <div className="user-info">
                                <img src={user.photoURL} alt="User" />
                                <p><Link className="profileButtonMain" to="/profile">{user.displayName}</Link></p>
                                <p><Link className="uploadButtonMain" to="/upload">Upload</Link></p>
                            </div>
                            <button className="logout-button" onClick={handleSignOut}>Logout</button>
                        </div>
                    )}
                </header>

                <Routes>
                    <Route path="/profile" element={<Profile user={user} images={images} onDelete={handleDelete} onLike={handleLike} />} />
                    <Route path="/upload" element={<Upload user={user} />} />
                    <Route path="/" element={
                        user ? (
                            <div className="masonry">
                                {images.map(image => (
                                    <div key={image.id} className="image-item" onClick={() => handleSelect(image)}>
                                        <img src={image.url} alt="" />
                                        <div className="image-item-info">
                                            <button onClick={(e) => { e.stopPropagation(); handleLike(image.id); }}>
                                                {image.likes && image.likes.includes(user.uid) ? "❤️" : "🤍"}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                                {selectedImage && isExpanded && (
                                    <div className="expandedImage" onClick={(e) => e.target === e.currentTarget && handleDeselect()}>
                                        <div className="expandedImageContainer">
                                            <img
                                                src={selectedImage.url}
                                                alt=""
                                                onDoubleClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDoubleLike(selectedImage.id);
                                                }}
                                            />
                                            {showHeart && <div className="heart">❤️</div>}
                                            <div className="image-item-info">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleLike(selectedImage.id);
                                                    }}
                                                >
                                                    {selectedImage.likes && selectedImage.likes.includes(user.uid) ? "❤️" : "🤍"}
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="login-form">
                                <h2>Sign In</h2>
                                <button className="googleButton" onClick={SignInWithGoogle}><img src="/img/googleIcon.png" alt="googleIcon" width="100%"/></button>
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
                        )
                    } />
                </Routes>
            </div>
        </Router>
    );
}


export default App;
