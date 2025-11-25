import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MentorService {

  private api = `${environment.backendUrl}/mentors`;

  constructor(private http: HttpClient) {}

  addAvailability(data: any): Observable<any> {
    return this.http.post(`${this.api}/availability`, data, { withCredentials: true });
  }

  getMyAvailability(): Observable<any> {
    return this.http.get(`${this.api}/my-availability`, { withCredentials: true });
  }

  deleteAvailability(id: number): Observable<any> {
    return this.http.delete(`${this.api}/availability/${id}`, { withCredentials: true });
  }

  getSlotsForAvailability(id: number): Observable<any> {
    var slots = this.http.get(`${this.api}/availability/${id}/slots`, { withCredentials: true });
    return slots
  }

  deleteSlot(slotId: number) {
  return this.http.delete(`${this.api}/slots/${slotId}`, {
    withCredentials: true
  });
}

getAllMentors() {
  return this.http.get(`${this.api}/mentors-list`, { withCredentials: true });
}

getSlots(mentorId: number, date: string): Observable<string[]> {
  return this.http.get<string[]>(`${this.api}/slots/${mentorId}?date=${date}`);
}

bookSlot(payload: any): Observable<any> {
    return this.http.post(`${this.api}/book-slot`, payload);
  }

 getMentorBookings() {
    return this.http.get(`${this.api}/bookings`);
  }
}
