import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = environment.backendUrl;   

  constructor(private http: HttpClient) { }

  // --- REGISTER ---
  register(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register`, data);
  }

  // --- LOGIN ---
  login(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login`, data);
  }

  // --- SAVE TOKEN ---
  saveToken(token: string) {
    localStorage.setItem('token', token);
  }

  // --- GET TOKEN ---
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  // --- LOGOUT ---
  logout() {
    localStorage.removeItem('token');
  }

  // --- CHECK LOGIN STATUS ---
  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }
}
