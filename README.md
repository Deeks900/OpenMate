******Backend Setup*******
cd backend
pip install -r requirements.txt

Create a .env file in backend having this content : 
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
DATABASE_URL=sqlite:///openmate.db

uvicorn main:app --reload

Check all end points here : http://127.0.0.1:8000/docs

****Frontend Setup*******
cd frontend
npm install
Create this file frontend/src/environments/environment.ts having below content 
Sign up here : https://cloudinary.com/
export const environment = {
  production: false,
  backendUrl: "http://127.0.0.1:8000",
  cloudinaryCloudName: 'signup on cloudinary to get this',
  cloudinaryUploadPreset: 'mentor_profiles'
};
ng serve --open


