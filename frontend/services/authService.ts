import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
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
