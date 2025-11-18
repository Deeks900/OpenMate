import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { tap, map } from 'rxjs/operators';


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
    return this.http.post(`${this.apiUrl}/auth/login`, data, {
      withCredentials: true
    }).pipe(
    tap((res: any) => {
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('user_role', res.role);
    })
  );
  }

  // --- SAVE TOKEN ---
  saveToken(token: string) {
    localStorage.setItem('access_token', token);
  }

  // --- GET TOKEN ---
  getToken(): string | null {
    var token = localStorage.getItem('access_token');
    console.log(token)
    return token
  }
    
  // --- LOGOUT ---
  logout() {
    localStorage.removeItem('access_token');
  }

  // --- CHECK LOGIN STATUS ---
  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  refreshToken() {
  return this.http.post<any>(`${this.apiUrl}/auth/refresh`, {}, { withCredentials: true })
    .pipe(
      tap(res => this.saveToken(res.access_token)),
      map(res => res.access_token)
    );
}

}
