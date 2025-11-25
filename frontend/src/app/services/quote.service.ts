import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { catchError, map, of } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class QuoteService {

  private apiUrl = environment.quoteUrl;
  private API_KEY = environment.quoteAPIKey;


  constructor(private http: HttpClient) {}

  getQuote(): Observable<any> {
     const headers = new HttpHeaders({
      'X-API-Key': this.API_KEY,
    });
    return this.http.get<any>(this.apiUrl, { headers })
    .pipe(
        map((res) => {
          if (res && res.length && res[0].quote) {
            return res[0];
          }
          return {
            quote: "Stay inspired and keep growing every day!",
            author: "OpenMate"
          };
        }),
        catchError(() =>
          of({
            quote: "Great things take time — keep going!",
            author: "OpenMate"
          })
        )
      );
  }
}
