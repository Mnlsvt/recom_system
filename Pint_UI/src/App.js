import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './App.css';

import { auth } from './firebaseAuth';
import firebase from 'firebase/compat/app';
import 'firebase/compat/auth';
import 'firebase/compat/firestore';
import 'firebase/compat/storage';
import Modal from 'react-modal';

import { getStorage, ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";



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


function Profile({ user, images, onDelete, onLike }) {
    const navigate = useNavigate();
    const userImages = images.filter(image => image.uploaderId === user.uid);
    const [isLoading, setIsLoading] = useState(true);

    const handleBack = () => {
        navigate('/');
    }

    const [modalIsOpen, setModalIsOpen] = useState(false);
    const fileInputRef = useRef();

    const openModal = () => {
        setModalIsOpen(true);
    }

    const closeModal = () => {
        setModalIsOpen(false);
    }

    const [selectedImage, setSelectedImage] = useState(null);

    const handleDelete = () => {
        if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            user.delete().then(() => {
                console.log("User deleted");
                // Redirect to the homepage after successful deletion
                navigate('/');
            }).catch((error) => {
                console.error("Error deleting user:", error);
            });
        }
    }


    const handleImageUpload = () => {
        if (selectedImage) {
            const storageRef = ref(storage, 'profilePictures/' + user.uid);
            const uploadTask = uploadBytesResumable(storageRef, selectedImage);

            uploadTask.on('state_changed', 
                (snapshot) => {
                    // You can use this section to display upload progress
                }, 
                (error) => {
                    console.log(error);
                }, 
                () => {
                    getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) => {
                        user.updateProfile({
                            photoURL: downloadURL
                        }).then(() => {
                            console.log('Profile picture updated');
                        }).catch((error) => {
                            console.log('Error updating profile picture: ', error);
                        });
                    });
                }
            );
        }
    }

    const handleImageChange = (e) => {
        if (e.target.files[0]) {
            setSelectedImage(e.target.files[0]);
            handleImageUpload();
        }
        closeModal();
    }


    const userImagesExists = userImages.filter(image => image.url); // Only images with url are included
    return (
        <div>
            <img src={user.photoURL || "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPuk1ANhAl5pGnajh1J2Jk83E0kVXsJtUy7Q&usqp=CAU"} width="2%" alt="User" onClick={openModal} style={{ cursor: 'pointer' }}/>
            <div>
                <Modal
                    isOpen={modalIsOpen}
                    onRequestClose={closeModal}
                    contentLabel="Profile Picture"
                    dialogClassName = "profileChange"
                >
                    <img src={user.photoURL} alt="Profile" style={{ width: '100%', height: 'auto' }} />
                    <button onClick={() => fileInputRef.current.click()}>Change Image</button>
                    <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleImageChange} />
                </Modal>
            </div>
            <button onClick={handleBack} className="back-button">Back</button>
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
            <button className="deleteAccount" onClick={handleDelete}>Delete My Account</button>
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



    const SignUpWithEmailPassword = (email, password, username) => {
        auth.createUserWithEmailAndPassword(email, password)
        .then((userCredential) => {
            // user successfully created, now set the username
            return userCredential.user.updateProfile({
                displayName: username
            })
            .then(() => {
                // Get the current user again after profile update
                const user = firebase.auth().currentUser;
                setUser(user);
            });
        })
        .catch((error) => {
            // Handle Errors here.
            var errorCode = error.code;
            var errorMessage = error.message;
            if (errorCode === 'auth/wrong-password') {
                alert('Wrong password.');
            } else {
                alert(errorMessage);
            }
            console.error(error);
        });
    }


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
                                <img src={user.photoURL || "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSPuk1ANhAl5pGnajh1J2Jk83E0kVXsJtUy7Q&usqp=CAU"} alt="User" />
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
                                <button className="googleButton" onClick={SignInWithGoogle}><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/1200px-Google_%22G%22_Logo.svg.png" alt="googleIcon" width="100%"/></button>
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
                                    SignUpWithEmailPassword(e.target.email.value, e.target.password.value, e.target.username.value);
                                }}>
                                    <input name="username" type="text" placeholder="Your Username" />
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
