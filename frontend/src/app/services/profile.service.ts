import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private api = `${environment.backendUrl}/profile`;

  constructor(private http: HttpClient) {}

  getMyProfile() {
    return this.http.get(`${this.api}/me`);
  }

  updateProfile(data: any) {
    console.log("I came on update Profile function.")
    console.log(data)
    return this.http.put(`${this.api}/update`, data);
  }
}
