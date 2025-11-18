import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class BookingService {

  private api = `${environment.backendUrl}/bookings`;

  constructor(private http: HttpClient) {}

  getMentorBookings(): Observable<any> {
    return this.http.get(`${this.api}/mentor`);
  }
}
