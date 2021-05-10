from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

def soundex(query: str):
    """
    https://en.wikipedia.org/wiki/Soundex
    :param query:
    :return:
    """

    # Step 0: Clean up the query string
    query = query.lower()
    letters = [char for char in query if char.isalpha()]

    # Step 1: Save the first letter. Remove all occurrences of a, e, i, o, u, y, h, w.

    # If query contains only 1 letter, return query+"000" (Refer step 5)
    if len(query) == 1:
        return query + "000"

    to_remove = ('a', 'e', 'i', 'o', 'u', 'y', 'h', 'w')

    first_letter = letters[0]
    letters = letters[1:]
    letters = [char for char in letters if char not in to_remove]

    if len(letters) == 0:
        return first_letter + "000"

    # Step 2: Replace all consonants (include the first letter) with digits according to rules

    to_replace = {('b', 'f', 'p', 'v'): 1, ('c', 'g', 'j', 'k', 'q', 's', 'x', 'z'): 2,
                  ('d', 't'): 3, ('l',): 4, ('m', 'n'): 5, ('r',): 6}

    first_letter = [value if first_letter else first_letter for group, value in to_replace.items()
                    if first_letter in group]
    letters = [value if char else char
               for char in letters
               for group, value in to_replace.items()
               if char in group]

    # Step 3: Replace all adjacent same digits with one digit.
    letters = [char for ind, char in enumerate(letters)
               if (ind == len(letters) - 1 or (ind+1 < len(letters) and char != letters[ind+1]))]

    # Step 4: If the saved letter’s digit is the same the resulting first digit, remove the digit (keep the letter)
    if first_letter == letters[0]:
        letters[0] = query[0]
    else:
        letters.insert(0, query[0])

    # Step 5: Append 3 zeros if result contains less than 3 digits.
    # Remove all except first letter and 3 digits after it.

    first_letter = letters[0]
    letters = letters[1:]

    letters = [char for char in letters if isinstance(char, int)][0:3]

    while len(letters) < 3:
        letters.append(0)

    letters.insert(0, first_letter)

    string = "".join([str(l) for l in letters])

    return string.upper()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content1 = db.Column(db.String(200), nullable=False)
    content2 = db.Column(db.String(200), nullable=False)
    content3 = db.Column(db.String(200), nullable=False)
    content4 = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/posts', methods = ['GET', 'POST'])
def posts():
    if request.method == 'POST':
        string_1 = request.form['string1']
        string_2 = request.form['string2']
        soundex_1 = soundex(string_1)
        soundex_2 = soundex(string_2)
        new_post = Todo(content1=string_1, content2=string_2, content3=soundex_1, content4=soundex_2)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
        
    else:
        all_strings = Todo.query.all()
        return render_template('index.html', names=all_strings)
    
@app.route('/posts/delete/<int:id>')
def delete(id):
    name = Todo.query.get_or_404(id)
    db.session.delete(name)
    db.session.commit()
    return redirect('/posts')


if __name__ == "__main__":
    app.run(debug=True)