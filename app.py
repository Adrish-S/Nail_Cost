from flask import Flask, render_template, request
import webview
app = Flask(__name__)
window = webview.create_window("AG Fasteners", app)

# Dictionary to store user selections
user_selections = {
    "RM Cost per kg": None,
    "Nail Type": None,
    "Nail Size": None,
    "Nail Quantity": None,
    "Nail Shank": None,
    "Nail Finish": None,
    "Final Cost": None,
}

# Dictionary to store available options
nail_options = {
    "21 Degree Plastic Collated": {
        "Sizes": ["2 x.113", "2-1/2 x.113", "2-3/8 x.113", "3 x.113", "2-1/2 x.120", "3 x.120", "3-1/4 x.120", "4 x.120", "2-1/2 x.131", "3 x.131", "3-1/4 x.131", "3-1/2 x.131"],
        "Quantity": ["1M", "3M", "4M", "5M"],
        "Shank Types": ["Smooth Shank", "Ring Shank"],
        "Finishes": ["Bright Finish", "HDG Finish"],
    },
    "15 Degree Coil Nail": {
        "Sizes": ["1-1/2 x.083", "1-3/4 x.083", "1-3/4 x.086", "1-3/4 x.092", "2 x.092", "2-3/16 x.092", "2-1/2 x.092", "2 x.099", "2-3/16 x.099", "2-1/2 x.099", "2-3/8 x.113", "3 x.120", "3-1/4 x.120"],
        "Quantity": ["2.5M", "3M", "4M", "5M", "7.5M", "9M", "14M"],
        "Shank Types": ["Smooth Shank", "Ring Shank", "Screw Shank"],
        "Finishes": ["Bright Finish", "EG Finish", "HDG Finish"],
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_selections["RM Cost per kg"] = request.form.get("rm_cost")
        user_selections["Nail Type"] = request.form.get("nail_type")
        user_selections["Nail Size"] = request.form.get("nail_size")
        user_selections["Nail Shank"] = request.form.get("nail_shank")
        user_selections["Nail Finish"] = request.form.get("nail_finish")
        user_selections["Nail Quantity"] = request.form.get("nail_quantity")
        margin_percentage = request.form.get("margin")
        if margin_percentage:
            margin_percentage = int(margin_percentage)
        else:
            # Set a default value (e.g., 8) if margin_percentage is empty
            margin_percentage = 8
        user_selections["Margin Percentage"] = margin_percentage
        usd_rate = float(request.form.get("rate"))

        final_cost = calculate_final_cost(
            user_selections["RM Cost per kg"],
            user_selections["Nail Type"],
            user_selections["Nail Size"],
            user_selections["Nail Shank"],
            user_selections["Nail Finish"],
            user_selections["Nail Quantity"],
            margin_percentage
        )
        user_selections["Final Cost"] = final_cost
        user_selections["USD Rate"] = round(final_cost/usd_rate, 2)
    margin_percentage = 8
    usd_rate = 0
    return render_template("index.html", user_selections=user_selections, nail_options=nail_options, margin_percentage=margin_percentage, usd_rate=usd_rate)

################################################################################################################################

def calculate_final_cost(rm_price, nail_type, nail_size, nail_shank, nail_finish, nail_quantity, margin_percentage):
    no_strips = 0
    no_coils = 0
    var1 = 0 # stores gm * no.strip // gm * coils per box
    total_wt = 0
    rm_cost = 0
    processing = 0

    ###########################################################################################
    #### RM Cost
    ## No of Strips
    if (nail_type == "21 Degree Plastic Collated"):
        if (nail_quantity == "5M"):
            no_strips = 179
        elif (nail_quantity == "4M"):
            no_strips = 143
        elif (nail_quantity == "3M"):
            no_strips = 120
        else:
            no_strips = 36 # 1M
    
    ## No of coils per box
    if (nail_type == "15 Degree Coil Nail"):
        if (nail_quantity == "2.5M"):
            no_coils = 16
        elif (nail_quantity == "3M"):
            no_coils = 20
        elif (nail_quantity == "4M"):
            no_coils = 20
        elif (nail_quantity == "4.5M"):
            no_coils = 30
        elif (nail_quantity == "5M"):
            no_coils = 0
        elif (nail_quantity == "7.5M"):
            no_coils = 0
        elif (nail_quantity == "9M"):
            no_coils = 0
        elif (nail_quantity == "12M"):
            no_coils = 0
        elif (nail_quantity == "14M"):
            no_coils = 0
        elif (nail_quantity == "16M"):
            no_coils = 40

    ## Gram for size of 21 Degree Plastic Collated
    if (nail_size == "2 x.113"):
        gm = 72
    elif (nail_size == "2-1/2 x.113"):
        gm = 91
    elif (nail_size == "2-3/8 x.113"):
        gm = 90
    elif (nail_size == "3 x.113"):
        gm = 109
    elif (nail_size == "2-1/2 x.120"):
        gm = 104
    elif (nail_size == "3 x.120"):
        gm = 125
    elif (nail_size == "3-1/4 x.120"):
        gm = 136
    elif (nail_size == "4 x.120"):
        gm = 167
    elif (nail_size == "2-1/2 x.131"):
        gm = 124
    elif (nail_size == "3 x.131"):
        gm = 148
    elif (nail_size == "3-1/4 x.131"):
        gm = 157
    elif (nail_size == "3-1/2 x.131"):
        gm = 172
    else:
        gm = -1
    var1 = (gm/1000) * no_strips
    total_wt = var1 * (1.040 if nail_shank == "Ring Shank" else 1.030)
    
    rm_cost = total_wt * float(rm_price)

####################################################################################################
    # Processing costs
    if (nail_type == "21 Degree Plastic Collated"):
        if(nail_finish == "Bright Finish"):
            processing += 37.75
            if(nail_shank == "Ring Shank"):
                processing += 10
        elif(nail_finish == "HDG Finish"):
            processing += 38.75
            if(nail_shank == "Ring Shank"):
                processing += 11

        finance_cost = (processing + float(rm_price))*(0.005)
        margin = (processing + float(rm_price))*(margin_percentage/100)
        processing_cost = processing + finance_cost + margin

    elif nail_type == "15 Degree Coil Nail":
        print("Working on it!")
    
    if (rm_cost > 0):
        total_cost = rm_cost + (processing_cost * total_wt)
    else:
        total_cost = -1.00
    return float(round(total_cost, 2))

#    fob_rate = total_cost / usd write this in another function

if __name__ == "__main__":
    #app.run(debug=True)
    webview.start()