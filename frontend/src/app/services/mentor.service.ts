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
    return this.http.post(`${this.api}/availability`, data);
  }

  getMyAvailability(): Observable<any> {
    return this.http.get(`${this.api}/my-availability`);
  }

  deleteAvailability(id: number): Observable<any> {
    return this.http.delete(`${this.api}/availability/${id}`);
  }

  getSlotsForAvailability(id: number): Observable<any> {
    var slots = this.http.get(`${this.api}/availability/${id}/slots`);
    return slots
  }

  deleteSlot(slotId: number) {
  return this.http.delete(`/mentors/slots/${slotId}`);
}

}
