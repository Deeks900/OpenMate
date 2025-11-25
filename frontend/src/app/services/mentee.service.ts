import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class MenteeService {
  private api = `${environment.backendUrl}/mentee`;
  constructor(private http: HttpClient) {}

  getMenteeBookings() {
  return this.http.get(`${this.api}/bookings`, { withCredentials: true });
}

}
