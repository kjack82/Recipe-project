from fastapi import FastAPI, HTTPException  ## need to import this when using FastApi and as will have HTTP exceptions, this needs to be imported too. 
import sqlite3  ## as using sqlite3
from typing import List ## use this to import List from typing module. 
from main import Recipes, UpdateRecipes ## import models from the main page. 

app = FastAPI()  ## app to run using fastapi - is required for FastApi to run. 

def get_db_connection():  ## this creates a connection to the db 
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row # allows access to columns by name, like accessing dictionary
    return conn ##returns the connection object. 

@app.get("/recipes/", response_model=List[Recipes])  ## GET request for all recipes in list
async def get_recipes():  #function created, no arguements required as not changing the state. 
    conn = get_db_connection() #connection to db 
    c = conn.cursor() #sets variable c to connection cursor
    c.execute('SELECT * FROM recipes') #command to select all from recipes database 
    recipes = c.fetchall() ##fetch all rows which has already been set above using conn.row_factory
    conn.close() #close connection 
    return [dict(recipe) for recipe in recipes] #returns response, this converts the rows to dictionaries, 
# this moves through the recipe list, for each recipe, in recipe list where recipe is a car object - it will convert it using dict(recipe)

@app.post("/recipes/", response_model=Recipes)  ##create new recipe
async def add_recipe(recipe: Recipes): ##needs arguements as needs to receive the info to process the request. hence recipe: Recipes
    conn = get_db_connection()
    c = conn.cursor() ## Below execute adds information to the following fields 
    c.execute('''
        INSERT INTO recipes (name, category, prep_time, rating, url, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (recipe.name, recipe.category, recipe.prep_time, recipe.rating, recipe.url, recipe.image_url))
    conn.commit()
    conn.close()
    return recipe # returns recipe response. As per below, simple conversion as no changes being made. 

@app.get("/recipes/{recipe_id}", response_model=Recipes)  
async def get_recipe(recipe_id: int): # = Path(..., description="The ID of the recipe you want to view"))
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone()
    conn.close()
    if recipe_id is None:
        raise HTTPException(status_code=404, detail="Recipe not found") #error message raised 
    return dict(recipe) #simple convertion to a dictionary required, as no changes are being made. 


@app.get("/get-by-name", response_model=List[Recipes]) ##get function to search by name 
async def get_recipe_by_name(name: str): # this time we have parameters as specific information is required and being searched)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM recipes WHERE name = ?', (name,))
    recipes = c.fetchall()
    conn.close()
    if not recipes: ##if no recipe
        raise HTTPException(status_code=404, detail="No recipe matching this name") ##raise exception 
    return [dict(recipe) for recipe in recipes] ##returns dictionary response 
    

@app.put("/recipes/{recipe_id}", response_model=Recipes) ##update receipe 
async def update_recipe(recipe_id: int, update: UpdateRecipes):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)) 
    recipe = c.fetchone()
    if recipe is None: #if no recipe
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found") #raise exception 

    updated_data = {key: value for key, value in update.dict().items() if value is not None}
    set_clause = ", ".join([f"{key} = ?" for key in updated_data.keys()])
    c.execute(f'UPDATE recipes SET {set_clause} WHERE id = ?', (*updated_data.values(), recipe_id))
    conn.commit()
    conn.close()
    return {**dict(recipe), **updated_data} ##this is used to merge two dictionaries. dict(recipe) relates to original db, updated data them updated info. Will allow an updated version 
#cnverts row (recipe) to a disctionary. ** used to open the key value pairsnthen creates a new dictionary whilst merging the two. 


@app.delete("/recipes/{recipe_id}", response_model=dict) ##delete request 
async def delete_recipe(recipe_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone() ##only one record required, rather than all. 
    if recipe is None: #if no recipe 
        conn.close()
        raise HTTPException(status_code=404, detail="Recipe not found") #close and raise exception
    
    c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,)) #otherwise execute deletion 
    conn.commit() #commit changes
    conn.close() #close connection 
    return {"message": "Recipe successfully deleted"} #confirm success via message 



