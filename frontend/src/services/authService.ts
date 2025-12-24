import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
  deleteUser,
  reauthenticateWithCredential,
  EmailAuthProvider,
  reauthenticateWithPopup,
} from "firebase/auth";
import { auth, googleProvider } from "../lib/firebase";

/**
 * Login user with email & password via Firebase Auth
 * Returns Firebase ID Token
 */
export const loginUser = async (email: string, password: string) => {
  const credential = await signInWithEmailAndPassword(auth, email, password);
  const token = await credential.user.getIdToken();
  return token;
};

/**
 * Sign up user with email, password, and display name
 * Returns Firebase ID Token
 */
export const signUpUser = async (
  email: string,
  password: string,
  displayName: string
) => {
  const credential = await createUserWithEmailAndPassword(
    auth,
    email,
    password
  );

  // Set the display name
  await updateProfile(credential.user, { displayName });

  const token = await credential.user.getIdToken();
  return token;
};

/**
 * Sign in with Google OAuth
 * Returns Firebase ID Token
 */
export const signInWithGoogle = async () => {
  const credential = await signInWithPopup(auth, googleProvider);
  const token = await credential.user.getIdToken();
  return token;
};

/**
 * Logout user and clear session
 */
export const logoutUser = async () => {
  await signOut(auth);
  localStorage.removeItem("token");
};

/**
 * Delete user account
 * Requires re-authentication for security
 */
export const deleteUserAccount = async (password?: string) => {
  const user = auth.currentUser;
  if (!user) {
    throw new Error("No user logged in");
  }

  // Re-authenticate based on provider
  const providerData = user.providerData[0];

  if (providerData?.providerId === "google.com") {
    // Re-authenticate with Google
    await reauthenticateWithPopup(user, googleProvider);
  } else if (providerData?.providerId === "password" && password && user.email) {
    // Re-authenticate with email/password
    const credential = EmailAuthProvider.credential(user.email, password);
    await reauthenticateWithCredential(user, credential);
  } else {
    throw new Error("Unable to verify identity. Please try again.");
  }

  // Delete the user
  await deleteUser(user);
  localStorage.removeItem("token");
};

/**
 * Get current user info
 */
export const getCurrentUser = () => {
  return auth.currentUser;
};

/**
 * Get user provider type
 */
export const getUserProvider = () => {
  const user = auth.currentUser;
  if (!user) return null;

  const providerData = user.providerData[0];
  return providerData?.providerId || null;
};
