import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../lib/firebase";

/**
 * Login user with email & password via Firebase Auth
 * Returns Firebase ID Token
 */
export const loginUser = async (email: string, password: string) => {
  const credential = await signInWithEmailAndPassword(
    auth,
    email,
    password
  );

  const token = await credential.user.getIdToken();
  return token;
};
