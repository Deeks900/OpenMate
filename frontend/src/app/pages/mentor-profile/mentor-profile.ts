import { Component } from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ProfileService } from '../../services/profile.service';
import { environment } from '../../../environments/environment';
import { Router } from '@angular/router';

@Component({
  selector: 'app-mentor-profile',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './mentor-profile.html',
  styleUrl: './mentor-profile.css',
})
export class MentorProfile {
  profileForm: any;
  previewUrl: string | null = null;
  selectedFile!: File;

  message: string = "";
  saving: boolean = false;

  constructor(private fb: FormBuilder, private profileService: ProfileService, private router: Router) {
    this.profileForm = this.fb.group({
      bio: ['', Validators.required],
      expertise: ['', Validators.required],
      public_slug: ['', Validators.required],
      photo_url: ['']
    });
  }

  // When user selects a photo
  onPhotoSelect(event: any) {
  this.selectedFile = event.target.files[0] as File;

  const reader = new FileReader();
  reader.onload = () => { this.previewUrl = reader.result as string };
  reader.readAsDataURL(this.selectedFile);
}


  // Upload to Cloudinary
  uploadToCloudinary(): Promise<string> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append("file", this.selectedFile!);
      formData.append("upload_preset", environment.cloudinaryUploadPreset);

      fetch(`https://api.cloudinary.com/v1_1/${environment.cloudinaryCloudName}/image/upload`, {
        method: "POST",
        body: formData
      })
      .then(res => res.json())
      .then(data => resolve(data.secure_url))
      .catch(err => reject(err));
    });
  }

  async saveProfile() {
    this.saving = true;
    this.message = "";

    try {
      let imageUrl = this.profileForm.value.photo_url;
      
      if (this.selectedFile) {
        imageUrl = await this.uploadToCloudinary();
      }
      
      console.log("I am creating the object to save")
      this.profileService.updateProfile({
        bio: this.profileForm.value.bio,
        expertise: this.profileForm.value.expertise,
        public_slug: this.profileForm.value.public_slug,
        photo_url: imageUrl
      }).subscribe(() => {
        this.message = "Profile saved successfully!";
        this.saving = false;
        this.router.navigate(['/dashboard']);
      });

    } catch (error) {
      this.message = "Failed to upload image. Try again.";
      this.saving = false;
    }
  }
}
