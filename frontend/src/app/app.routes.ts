import { Routes } from '@angular/router';
import { Login } from './pages/login/login';
import { Register } from './pages/register/register';
import { MentorProfile } from './pages/mentor-profile/mentor-profile';
import { MentorProfileEdit } from './pages/mentor-profile-edit/mentor-profile-edit';
import { Dashboard } from './pages/dashboard/dashboard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'mentor/profile', component: MentorProfile },
  { path: 'mentor/profile-edit', component: MentorProfileEdit},
  { path: 'dashboard', component: Dashboard}

];
