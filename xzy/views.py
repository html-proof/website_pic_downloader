import os
from django.shortcuts import render
from instaloader import Instaloader, Profile, ProfileNotExistsException
from urllib3.exceptions import ConnectTimeoutError

def is_valid_url(url):
    return url.startswith('https://www.instagram.com/')  # Basic validation for Instagram profile URL

def num(request):
    if request.method == 'POST':
        profile_url = request.POST.get('profileUrl')
        profile_picture_url = ""
        success_message = ""
        similar_profiles = []

        if profile_url and is_valid_url(profile_url):  # Check if the URL is not empty and valid
            instaloader = Instaloader()

            try:
                # Extract the username from the profile URL
                username = profile_url.strip('/').split('/')[-1]
                
                # Get the Instagram profile
                profile = Profile.from_username(instaloader.context, username)
                
                # Fetch the profile picture URL
                profile_picture_url = profile.profile_pic_url

                success_message = f"Profile picture fetched successfully for {profile_url}"

                # Find similar profiles based on follower count
                target_followers = set(profile.get_followers())
                target_followees = set(profile.get_followees())
                similar_profiles = []

                for p in instaloader.get_profiles():
                    if p.username != username:  # Exclude the same profile
                        other_followers = set(p.get_followers())
                        other_followees = set(p.get_followees())
                        
                        common_followers = len(target_followers.intersection(other_followers))
                        common_followees = len(target_followees.intersection(other_followees))
                        
                        # Adjust the threshold values as needed
                        if 1000 <= common_followers <= 5000 or 1000 <= common_followees <= 5000:
                            similar_profiles.append(p.username)

            except ProfileNotExistsException:
                success_message = f"Profile {username} does not exist."
            except ConnectTimeoutError:
                success_message = "Error: Connection to Instagram timed out. Please try again later."
            except Exception as e:
                pass
        elif not profile_url:
            success_message = "Please enter an Instagram profile URL."
        else:
            success_message = "Invalid Instagram profile URL"

        return render(request, 'num.html', {'success_message': success_message, 'profile_picture_url': profile_picture_url, 'similar_profiles': similar_profiles})

    return render(request, 'num.html', {'success_message': '', 'profile_picture_url': '', 'similar_profiles': []})
