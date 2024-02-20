# Υποχρεωτική Εργασία -  Δικτυοκεντρικά Πληροφοριακά Συστήματα

## Αναλυτική Περιγραφή της εργασίας στο Greek Documentation.pdf 
## Τρόπος Εκτέλεσης 
### ΒΗΜΑ 1: Εγκατάσταση Python
Μπορείτε να κατεβάσετε και να εγκαταστήσετε την Python από [εδώ](https://www.python.org/downloads/).

### ΒΗΜΑ 2: Εγκατάσταση Flask
Για την εγκατάσταση του Flask, εκτελέστε την ακόλουθη εντολή στο τερματικό: pip install Flask

### ΒΗΜΑ 3: Εγκατάσταση του pymongo
Για την εγκατάσταση του pymongo, εκτελέστε την ακόλουθη εντολή στο τερματικό: pip install pymongo

### ΒΗΜΑ 4: Εγκατάσταση του requests
Για την εγκατάσταση του requests, εκτελέστε την ακόλουθη εντολή στο τερματικό: pip install requests

### ΒΗΜΑ 5: Εγκατάσταση του bson
Για την εγκατάσταση του bson, εκτελέστε την ακόλουθη εντολή στο τερματικό: pip install bson

### ΒΗΜΑ 6: Εγκατάσταση MongoDB
Μπορείτε να κατεβάσετε και να εγκαταστήσετε την MongoDB από [εδώ](https://www.mongodb.com/try/download/community).

### ΒΗΜΑ 7: Εγκατάσταση MongoDB Tools
Μπορείτε να κατεβάσετε και να εγκαταστήσετε τα MongoDB Tools από [εδώ](https://www.mongodb.com/try/download/database-tools).

### ΒΗΜΑ 8: Φόρτωση Δεδομένων στη Βάση Δεδομένων
Για τη φόρτωση δεδομένων στη Βάση Δεδομένων, εκτελέστε τις ακόλουθες εντολές στο τερματικό:
1. Αντικαταστήστε το `pathTo` με τον απόλυτο διαδρομή στον φάκελο του έργου.
2. Τρέξτε τις παρακάτω εντολές:
```shell
mongoimport --db Gym --collection users --jsonArray --file pathTo/GymManSystem/my_db/users.json
mongoimport --db Gym --collection trainers --jsonArray --file pathTo/GymManSystem/my_db/trainers.json
mongoimport --db Gym --collection services --jsonArray --file pathTo/GymManSystem/my_db/services.json
mongoimport --db Gym --collection announcements --jsonArray --file pathTo/GymManSystem/my_db/announcements.json
mongoimport --db Gym --collection reservations --jsonArray --file pathTo/GymManSystem/my_db/reservations.json
```

### ΒΗΜΑ 9: Εκτέλεση της Εφαρμογής
Για να τρέξετε την εφαρμογή, εκτελέστε την ακόλουθη εντολή από τον κατάλογο του έργου:

```shell
python app.py
```
Η εφαρμογή θα είναι διαθέσιμη στη διεύθυνση http://localhost:5000/homeHTML.
Η εφαρμογή τρέχει στην πόρτα 5000 με Flask και η MongoDB στην πόρτα 27017.
