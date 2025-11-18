import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ProfileService {
  private api = `${environment.backendUrl}/profile`;

  constructor(private http: HttpClient) {}

  getMyProfile():Observable<any> {
    return this.http.get<any>(`${this.api}/me`);
  }

  updateProfile(data: any):Observable<any>{
    console.log("I came on update Profile function.")
    console.log(data)
    return this.http.put<any>(`${this.api}/update`, data);
  }
}
