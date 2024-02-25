const fetchUserPreferences = async (userId, db) => {
    // Reference to the user's document in the 'users' collection
    const userRef = db.collection('users').doc(userId);

    try {
        const doc = await userRef.get();
        if (doc.exists) {
            // Assuming preferences are stored in a field named 'preferences'
            const preferences = doc.data().preferences;
            return preferences; // This should be an object like { nature: 3, cars: 5, movies: 1 }
        } else {
            console.log('No such user document!');
            return {}; // Return an empty object if the user document doesn't exist
        }
    } catch (error) {
        console.error('Error fetching user preferences:', error);
        throw error; // Rethrow the error for calling function to handle
    }
};



export const fetchImagesForUser = async (userId, db, startAfter, totalImagesToFetch, fetchedIds) => {
    const PREFERENCE_RATIO = 0.7; // 70% images based on preferences
    const WEIGHTS = [0.5, 0.3, 0.2]; // Weights for top 3 categories
    const preferences = await fetchUserPreferences(userId, db);
    const sortedPreferences = Object.entries(preferences).sort((a, b) => b[1] - a[1]);

    let lastDoc = startAfter;
    let images = [];
    let currentFetchedIds = [];

    // Fetch images based on top categories with different weights
    for (let i = 0; i < 3; i++) {
        const [category, _] = sortedPreferences[i];
        const categoryImagesToFetch = Math.floor(totalImagesToFetch * PREFERENCE_RATIO * WEIGHTS[i]); // Use Math.floor instead of Math.ceil

        let query = db.collection('images').where('metadata.predicted_class', '==', category);
        if (lastDoc) {
            query = query.startAfter(lastDoc);
        }
        query = query.limit(categoryImagesToFetch);

        const snapshot = await query.get();
        console.log(`Fetching ${categoryImagesToFetch} images from category: ${category}`);

        snapshot.forEach((doc) => {
            if (!fetchedIds.has(doc.id)) {
                images.push({ ...doc.data(), id: doc.id });
                lastDoc = doc; // Update lastDoc with the current document
                currentFetchedIds.push(doc.id);
            } else {
                console.log('Duplicate image skipped:', doc.id);
            }
        });
    }

    // Debugging: Log fetched image IDs
    // console.log('Fetched image IDs:', images.map(img => img.id));

    // Fetch the rest of the images without category preference
    let randomImagesToFetch = totalImagesToFetch - images.length;

    if (randomImagesToFetch > 0) {
        let query = db.collection('images').orderBy('metadata.timestamp');

        if (lastDoc) {
            query = query.startAfter(lastDoc);
        }

        query = query.limit(randomImagesToFetch);
        const snapshot = await query.get();

        snapshot.forEach(async (doc) => {
            if (!fetchedIds.has(doc.id) && !currentFetchedIds.includes(doc.id)) {
                images.push({ ...doc.data(), id: doc.id });
                lastDoc = doc;
                console.log(`Fetched random image from category: ${doc.data().metadata.predicted_class}`);
            } else {
                console.log('Skipped image:', doc.id);
            }
        });

        if (snapshot.empty) {
            console.log("No more images to fetch.");
        }
    }

    console.log(`Total images fetched: ${images.length}`);
    console.log('Fetched image IDs:', images.map(img => img.id));
    return { images, lastDoc };
};


// Usage
/*firebase.auth().onAuthStateChanged(async (user) => {
    if (user) {
        const images = await fetchImagesForUser(user.uid);
        displayImages(images);
    }
});*/
