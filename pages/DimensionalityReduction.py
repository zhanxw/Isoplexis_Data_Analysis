#from sklearn.manifold import TSNE
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from dash import no_update
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import dash
from openTSNE import TSNE

# methods for PCA and TSNE
method_pcatsne = ["Standard Scalar Normalized", "Not Normalized"]
# values neccessary for tsne function
iterations = [250, 300, 400, 500, 600, 700, 800, 900, 1000]
perplexity = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
plot_types = ["2D", "3D"]
centerStyle = {"textAlign": "center"}

layout = html.Div(
    [
        html.H2("Dimensionality Reduction", style=centerStyle),
        html.Div(
            [
                html.H4("Introduction"),
                html.P(
                    "PCA is a linear dimensionality reduction technique and TSNE is a non-linear dimensionality reduction technique."
                ),
                html.P(
                    [
                        html.I(className="fa fa-sticky-note"),
                        "Note: Dimensionality reduction analyses may differ from  IsoSpeak. IsoSpeak uses unthresholded data, while the data file the user uploaded has a 2% threshold. Values below this threshold become 0.",
                    ]
                ),
                html.P(
                    "TSNE might take a minute to reload since this is calculated in real-time."
                ),
            ],
            className="shadow p-3 mb-5 bg-white rounded",
        ),
        html.Div(
            [
                html.H4(
                    "Select whether or not to normalize dimensionality reduction plots."
                ),
                html.P(
                    "Data is normally normalized before performing dimensionality reduction."
                ),
                dcc.RadioItems(
                    id="method_radio",
                    options=method_pcatsne,
                    value="Standard Scalar Normalized",
                    inline=True,
                    inputStyle={"margin-right": "5px", "margin-left": "5px"},
                    style=centerStyle,
                ),
                html.H4("Select to visualize the plot in 2D or 3D."),
                dcc.RadioItems(
                    id="plot_types",
                    options=plot_types,
                    value="3D",
                    inline=True,
                    inputStyle={"margin-right": "5px", "margin-left": "5px"},
                    style=centerStyle,
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                html.Div(dcc.Graph(id="dim_red_fig")),
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div(
                                        dcc.Loading(
                                            id="loading-tsne",
                                            children=dcc.Graph(id="ts_dim_red_fig"),
                                        )
                                    ),
                                    html.H6("Select Perplexity of Nearest Neighbors: "),
                                    html.P(
                                        "Perplexity is the balance between local and global aspects of the data."
                                    ),
                                    dcc.RadioItems(
                                        id="perplexity_radio",
                                        options=perplexity,
                                        value=30,
                                        inline=True,
                                        inputStyle={
                                            "margin-right": "5px",
                                            "margin-left": "5px",
                                        },
                                        style=centerStyle,
                                    ),
                                    html.Br(),
                                    html.H6("Select Number of TSNE Iterations: "),
                                    html.P(
                                        [
                                            html.I(className="fa fa-sticky-note"),
                                            "Note: The more iterations performed, the slower the algorithm runs.",
                                        ]
                                    ),
                                    dcc.RadioItems(
                                        id="iterations_radio",
                                        options=iterations,
                                        value=500,
                                        inline=True,
                                        inputStyle={
                                            "margin-right": "5px",
                                            "margin-left": "5px",
                                        },
                                        style=centerStyle,
                                    ),
                                ]
                            ),
                            width=6,
                        ),
                    ]
                ),
            ],
            className="shadow p-3 mb-5 bg-white rounded",
        ),
    ]
)

# callback: pca function


@callback(
    Output("dim_red_fig", "figure"),
    Input("analysis-button", "n_clicks"),
    Input("method_radio", "value"),
    Input("plot_types", "value"),
    Input("cyto_list", "data"),
    State("filtered-data", "data"),
    State("color_discrete_map", "data"),
)
def pca_func(n, method, plot_type, cytokines, df, color_discrete_map):
    try:
        if n is None:
            return no_update
        else:
            df = pd.DataFrame(df)
            Y = df.loc[:, ["Treatment Conditions"]].values
            x = df.loc[:, cytokines].values
            # # Separating out the target
            if method == "Standard Scalar Normalized":
                x = StandardScaler().fit_transform(x)
            pca = PCA(n_components=3)
            principalComponents = pca.fit_transform(x)
            # Determine explained variance using explained_variance_ration_ attribute
            exp_var_pca = pca.explained_variance_ratio_
            df = pd.DataFrame(principalComponents)
            df2 = df.rename({0: "PCA 1"+ ' (' + str("{:.2f}".format(exp_var_pca[0]*100)) +'%)', 
                    1: "PCA 2"+ ' (' + str("{:.2f}".format(exp_var_pca[1]*100)) +'%)', 
                    2: "PCA 3" + ' (' + str("{:.2f}".format(exp_var_pca[2]*100)) +'%)'}, axis=1)
            df2["Treatment Conditions"] = [ i[0] for i in Y ]
            if plot_type == "2D":
                fig = px.scatter(
                    df2,
                    x="PCA 1" + ' (' + str("{:.2f}".format(exp_var_pca[0]*100)) +'%)',
                    y="PCA 2" + ' (' + str("{:.2f}".format(exp_var_pca[1]*100)) +'%)',
                    color="Treatment Conditions",
                    color_discrete_map=color_discrete_map,
                )
                totalexplainedvariance = (exp_var_pca[0] + exp_var_pca[1])*100
            else:
                fig = px.scatter_3d(
                    df2,
                    x="PCA 1" + ' (' + str("{:.2f}".format(exp_var_pca[0]*100)) +'%)',
                    y="PCA 2" + ' (' + str("{:.2f}".format(exp_var_pca[1]*100)) +'%)',
                    z="PCA 3" + ' (' + str("{:.2f}".format(exp_var_pca[2]*100)) +'%)',
                    color="Treatment Conditions",
                    color_discrete_map=color_discrete_map,
                )
                totalexplainedvariance = (exp_var_pca[0] + exp_var_pca[1] + exp_var_pca[2])*100
            fig.update_layout(
                title_text=method + " PCA" + ' (Total Explained Variance: ' + str("{:.2f}".format(totalexplainedvariance)) + '%)',
                title_x=0.5)
            fig.update_layout(plot_bgcolor="rgb(255,255,255)")
            fig.update_traces(marker={"size": 5})
            # fig.update_layout(width=800, height=800)
            return fig
    except:
        print("Error in PCA function!!!")
        return no_update


# callback: tsne function
@callback(
    Output("ts_dim_red_fig", "figure"),
    Input("analysis-button", "n_clicks"),
    Input("method_radio", "value"),
    Input("plot_types", "value"),
    Input("perplexity_radio", "value"),
    Input("iterations_radio", "value"),
    Input("cyto_list", "data"),
    State("filtered-data", "data"),
    State("color_discrete_map", "data"),
)
def tsne_func(
    n, method, plot_type, perplexity, iterations, cytokines, df, color_discrete_map
):
    try:
        if n is None:
            return no_update

        else:
            df = pd.DataFrame(df)
            #Y = df.loc[:, ["Treatment Conditions"]].values
            x = df.loc[:, cytokines].values
            #x = df[cytokines]
            Y = df["Treatment Conditions"].astype(str)
            # # Separating out the target
            if method == "Standard Scalar Normalized":
                x = StandardScaler().fit_transform(x)
            pca = PCA()
            principalComponents = pca.fit_transform(x)
            # tsne = TSNE(
            #     n_components=3, perplexity=perplexity, n_iter=iterations
            # ).fit_transform(principalComponents)
            #new TSNE implementation
            tsne = TSNE(
                n_components=3,
                perplexity=perplexity,
                metric="euclidean",
                n_jobs=8,
                random_state=42,
                verbose=True,
                n_iter=iterations
                )
            tsne_1 = tsne.fit(principalComponents)
            #tsne_2 = tsne.transform(tsne_1)
            
            
            df = pd.DataFrame(tsne_1)
            df2 = df.rename({0: "TSNE 1", 1: "TSNE 2", 2: "TSNE 3"}, axis=1)
            df2["Treatment Conditions"] = Y
            if plot_type == "2D":
                fig = px.scatter(
                    df2,
                    x="TSNE 1",
                    y="TSNE 2",
                    color="Treatment Conditions",
                    color_discrete_map=color_discrete_map,
                )
            else:
                fig = px.scatter_3d(
                    df2,
                    x="TSNE 1",
                    y="TSNE 2",
                    z="TSNE 3",
                    color="Treatment Conditions",
                    color_discrete_map=color_discrete_map,
                )
            fig.update_layout(
                title_text=method + " TSNE",
                title_x=0.5,
            )
            fig.update_layout(plot_bgcolor="rgb(255,255,255)")
            fig.update_traces(marker={"size": 5})
            #fig.update_layout(width=800, height=800)
            return fig
    except:
        return no_update
