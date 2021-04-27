from flask_restful import Resource

from models.site import SiteModel


class Sites(Resource):
    # /sites
    def get(self):
        return {'sites': [site.json() for site in SiteModel.query.all()]}, 200


class Site(Resource):
    # /sites/{url}
    def get(self, url):
        site = SiteModel.find_site(url)
        if site:
            return site.json()
        return {'message': 'Site not found.'}, 404

    def post(self, url):
        if SiteModel.find_site(url):
            return {"message": "Site '{}' already exists.".format(url)}, 400
        site = SiteModel(url)
        try:
            site.save_site()
        except Exception:
            return {'message': 'An internal error ocurred trying to save site'}, 500
        return site.json(), 200

    def delete(self, url):
        site = SiteModel.find_site(url)
        if site:
            try:
                site.delete_site()
            except Exception:
                return {'message': 'An internal error ocurred trying to delete site'}, 500
            return {"message": "Site id '{}' deleted.".format(url)}, 200
        return {"message": "Site '{}' not found.".format(url)}, 404
